# sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-vbattb.c

Purpose: This platform driver registers clocks for the Renesas VBATTB block, including the low-speed crystal gate, bypass fixed factor, mux, and critical VBATTCLK output for RTC counter use.

Important APIs, types, and functions: The driver defines `struct vbattb_clk`, load-capacitance constants, `vbattb_clk_validate_load_capacitance()`, cleanup action `vbattb_clk_action()`, and `vbattb_clk_probe()`. It uses devm CCF helpers for gate, fixed-factor, mux, and parent-hw gate clocks.

Control flow: Probe reads `quartz-load-femtofarads` with a 4 pF default, validates it, allocates clock data, maps MMIO, enables PM runtime, obtains and deasserts a shared reset, registers a cleanup action, creates four clocks, programs oscillator load capacitance, marks `vbattclk` critical, and adds an OF onecell provider.

State and persistence: Hardware state includes VBATTB registers for source select, oscillator stop, oscillator output enable, and load capacitance. Runtime PM and reset state are active while the provider exists. Cleanup asserts reset, runtime-suspends, and removes the clock provider.

Dependencies and integration: Depends on platform bus, PM runtime, reset framework, CCF devm helpers, OF, and `renesas,r9a08g045-vbattb.h`. RTC consumers depend on `VBATTB_VBATTCLK`.

Risks: The cleanup error message says "de-assert" while asserting reset, a minor diagnostic bug. Invalid capacitance values fail probe. `vbattclk` is critical, so it will not be disabled by unused-clock cleanup. Ordering of capacitance programming before output registration matters.

Test signals: Probe with each supported capacitance, check invalid DT value fails, verify reset/runtime PM balance on unbind, inspect four exported clocks, and confirm RTC remains functional through unused-clock cleanup and suspend/resume.
