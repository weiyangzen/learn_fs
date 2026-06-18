# sources/distributed-fs/ceph-client/drivers/clk/clk-apple-nco.c

## Purpose
Implements Apple SoC numerically controlled oscillator channels as programmable CCF clocks. The driver translates desired rates into NCO divisor and accumulator increment registers, including the LFSR encoding used for coarse divisors.

## Important APIs, Types, And Functions
Important types are `applnco_tables` and `applnco_channel`. Core helpers include `applnco_compute_tables`, `applnco_div_out_of_range`, `applnco_div_translate`, `applnco_div_translate_inv`, `applnco_set_rate`, `applnco_recalc_rate`, `applnco_determine_rate`, enable/disable/is_enabled callbacks, and `applnco_probe`.

## Control Flow
Probe maps the register resource, derives the number of channels from resource size and channel stride, allocates onecell data and shared translation tables, initializes each channel with its own lock and base offset, registers one clock per channel with parent index 0, then adds an OF onecell provider. Rate set computes a base divisor and two accumulator increments, validates/encodes the divisor, disables the channel under lock, writes divider/increment/accumulator initial registers, and restores enable state.

## State And Persistence
Each channel stores base, shared LFSR tables, `clk_hw`, and a spinlock. Hardware registers persist enable, encoded divisor, increments, and accumulator initial value. CCF provider state persists through devm lifetime.

## Dependencies And Integration Points
Depends on platform resources, OF compatibles `apple,t8103-nco` and `apple,nco`, CCF onecell providers, bitfield helpers, math64 division, and spinlocks.

## Risks And Edge Cases
The operation theory is partly inferred. Unsupported accumulator wraparound or zero increments make recalc return zero. Very low or high requested rates can put the coarse divisor out of range. Rate programming temporarily disables the channel, which may glitch consumers.

## Test Signals
Check LFSR forward/inverse table round trips, min/max determine-rate clamping, set/recalc consistency for representative parent rates, enable preservation across set_rate, multi-channel resource sizing, and rejection of out-of-range divisors.
