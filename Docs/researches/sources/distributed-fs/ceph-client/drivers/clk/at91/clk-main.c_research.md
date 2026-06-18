# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-main.c

Purpose: providers for AT91 main clock sources: external main oscillator, internal main RC oscillator, legacy RM9200 main clock, and SAM9x5 muxable main clock.

Important APIs and data: exported helpers are `at91_clk_register_main_osc()`, `at91_clk_register_main_rc_osc()`, `at91_clk_register_rm9200_main()`, and `at91_clk_register_sam9x5_main()`. Private structs store regmap, cached RC frequency/accuracy, parent selection, and power-management status.

Control flow: oscillator prepare sets MOR key-protected enable/bypass bits and waits for `MOSCS`; unprepare clears enable. RC prepare enables `MOSCRCEN` and waits for `MOSCRCS`. RM9200/SAM9x5 main clocks probe frequency through `CKGR_MCFR`, using busy wait before boot and sleep later. SAM9x5 set_parent toggles `MOSCSEL` and waits for `MOSCSELS`.

State and persistence: RC frequency/accuracy are static properties; main mux parent is read from hardware at registration. Save/restore records enabled state and parent for backup suspend and replays preparation/parent selection when needed.

Dependencies and integration: heavily used by every SoC setup and DT compat path. It depends on key-protected MOR writes (`AT91_PMC_KEY`), PMC status bits, delay helpers, and common-clock parent data/name support.

Risks: several waits are unbounded except MCFR probing timeout; wrong parent rate can make main frequency fallback approximate; `clk_sam9x5_main_save_context()` calls RC helper on a SAM9x5 main struct layout, which is fragile but intentionally relies on shared first fields. Test signals include main clock parent switching, MCFR timeout logs, RC accuracy propagation, and suspend/resume restoring oscillator state.
