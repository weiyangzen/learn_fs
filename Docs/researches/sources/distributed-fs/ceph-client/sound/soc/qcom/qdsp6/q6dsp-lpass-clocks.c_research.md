# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6dsp-lpass-clocks.c

Purpose: `q6dsp-lpass-clocks.c` adapts QDSP6 LPASS clock and hardware-block vote operations into the Linux common clock framework.

Important APIs and types: `struct q6dsp_clk` wraps one clock hardware object with QDSP6 clock ID, attributes, cached rate, vote handle, and device. `struct q6dsp_cc` stores the provider, clock array, and `q6dsp_clk_desc`. Clock ops are split between rate-bearing clocks (`clk_q6dsp_ops`) that call `lpass_set_clk` on prepare/unprepare and vote-only clocks (`clk_vote_q6dsp_ops`) that call `lpass_vote_clk`/`lpass_unvote_clk`. The exported entry is `q6dsp_clock_dev_probe`.

Control flow: probe reads the match-data descriptor, allocates provider state, creates a `clk_hw` for each descriptor entry, chooses ops based on whether an initial rate is nonzero, registers each clock, and adds an OF clock provider. OF lookup validates index and attribute arguments, stores the requested attribute in the clock, and returns its `clk_hw`.

State and persistence: cached rate and last-requested attributes live in `struct q6dsp_clk`. Vote handles are stored after prepare and reused for unprepare. Registered clocks persist for the platform device lifetime through devm allocations.

Dependencies and integration points: descriptors come from platform-specific drivers using `q6dsp-lpass-clocks.h`. Function pointers usually target AFE/APM clock/vote helpers. The OF provider expects two-cell clock specifiers: clock index and attribute.

Risks: `clk_q6dsp_determine_rate` returns 0 without constraining `req`, so consumers may believe any rate is acceptable. Attribute is mutable per OF lookup on a shared clock object; multiple consumers with different attributes can race or override each other. `Q6DSP_MAX_CLK_ID` must cover all descriptor `clk_id` values.

Test signals: register descriptors with valid/invalid IDs, prepare/unprepare rate clocks and vote clocks, set/recalc rate, OF lookup with invalid attribute, and multi-consumer attribute behavior.
