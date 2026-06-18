# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6dsp-lpass-clocks.h

Purpose: `q6dsp-lpass-clocks.h` defines descriptor structures for registering QDSP6 LPASS clocks with the common helper in `q6dsp-lpass-clocks.c`.

Important APIs and types: `struct q6dsp_clk_init` describes one clock: Linux provider index, firmware QDSP6 clock ID or hardware block ID, name, and optional default rate. `Q6DSP_VOTE_CLK` builds a vote-only descriptor with no rate. `struct q6dsp_clk_desc` contains the descriptor array, count, and function pointers for setting, voting, and unvoting LPASS clocks. `q6dsp_clock_dev_probe` is declared for reuse by platform drivers.

Control flow: platform drivers provide a `q6dsp_clk_desc` as OF match data and call `q6dsp_clock_dev_probe` from their probe function.

State and persistence: no state in the header; descriptors are usually static const data in platform-specific code.

Dependencies and integration points: depends on platform devices and callback implementations from AFE/APM service layers. Consumers use OF clock specifiers resolved by the C file.

Risks: function pointer contracts are not type-rich enough to distinguish rate clocks from vote-only clocks; descriptor rate zero is the discriminator. Bad `clk_id` values fail later at probe or lookup.

Test signals: compile descriptor users, probe with mixed rate/vote clocks, and confirm callbacks are invoked with expected IDs and attributes.
