# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6afe-clocks.c

## Purpose
`q6afe-clocks.c` exposes Q6AFE LPASS clocks and core hardware votes as Linux clocks through the common Q6DSP clock provider. It translates clock framework operations into Q6AFE DSP clock set/vote/unvote commands.

## Important APIs, types, and functions
The `Q6AFE_CLK(id)` macro creates `struct q6dsp_clk_init` entries with Linux-facing clock IDs, Q6AFE DSP clock IDs, names, and a default 19.2 MHz rate. `q6afe_clks[]` enumerates MI2S, PCM, TDM, MCLK, codec core, WSA, VA, TX, RX, and vote clocks. `q6dsp_clk_q6afe` binds the table to `q6afe_set_lpass_clock()`, `q6afe_vote_lpass_core_hw()`, and `q6afe_unvote_lpass_core_hw()`.

## Control flow
The platform driver matches `qcom,q6afe-clocks` and calls the shared `q6dsp_clock_dev_probe()` with the descriptor from OF match data. From then on, clock framework consumers interact with clocks registered by the common provider, which calls back into Q6AFE helpers for DSP-side clock control.

## State and persistence behavior
This file has static const clock descriptors only. Runtime clock state is managed by the common Q6DSP clock provider and DSP firmware. No disk state is used.

## Dependencies and integration points
The driver depends on Q6AFE clock IDs from DT bindings, `q6dsp-lpass-clocks.h`, and Q6AFE clock/vote functions from `q6afe.h`. It integrates with device-tree clock providers and consumers such as QDSP6 AFE DAI or machine drivers that request LPASS clocks.

## Risks and test signals
Risks include missing clock IDs, incorrect default rates, or wrong vote block IDs, causing audio interfaces to fail only when a specific bus/codec clock is needed. Test signals include DT clock lookup, enable/disable traces for MI2S/TDM/codec clocks, vote/unvote balance, and allmodconfig build coverage.
