## sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi6220-stub.c

### Purpose
`clk-hi6220-stub.c` implements a firmware-mediated Hi6220 CPU clock. It exposes the ACPU0 rate through the common clock framework while reading and writing DFS state in SRAM and notifying firmware over a mailbox.

### Important APIs, Types, And Functions
`struct hi6220_stub_clk` stores the clock ID, device, `clk_hw`, DFS regmap, mailbox client, and channel. `hi6220_acpu_get_freq()`, `hi6220_acpu_set_freq()`, and `hi6220_acpu_round_freq()` are the SRAM/mailbox helpers. `hi6220_stub_clk_recalc_rate()`, `hi6220_stub_clk_determine_rate()`, and `hi6220_stub_clk_set_rate()` are the clock ops. `hi6220_stub_clk_probe()` registers the provider.

### Control Flow
Probe obtains the SRAM syscon regmap from `hisilicon,hi6220-clk-sram`, configures a blocking mailbox client, requests channel 0, registers a no-parent clock named `acpu0`, publishes it as a simple OF provider, and clears DFS request/limit fields. Rate changes convert Hz to kHz, write `ACPU_DFS_FREQ_REQ`, compose a mailbox frequency-set message, and send it.

### State, Persistence, And Dependencies
State is split between the driver object, DFS SRAM registers, and firmware behavior behind the mailbox. Current rate is read from `ACPU_DFS_CUR_FREQ`. The file depends on syscon/regmap, mailbox, OF platform probing, and firmware-compatible SRAM layout.

### Integration Points
CPUFreq or other clock consumers can request ACPU0 rate changes via CCF. The firmware side is responsible for applying the mailbox request and updating current frequency.

### Risks
Only `HI6220_STUB_ACPU0` is implemented despite additional ID defines. `mbox_send_message()` return is ignored, so failed firmware delivery can look successful. `WARN_ON(freq > max_freq)` clamps but also emits warnings for normal over-requests. Unit mismatch errors would be severe because SRAM values are kHz and CCF rates are Hz.

### Test Signals
Validate CPU rate readback and rate changes through clk debugfs or cpufreq, mailbox timeout/error behavior, SRAM limit clamping, and boot logs for syscon/mailbox provider failures.
