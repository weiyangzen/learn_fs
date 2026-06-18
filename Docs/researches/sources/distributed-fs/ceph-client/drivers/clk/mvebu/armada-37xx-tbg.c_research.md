# sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-37xx-tbg.c

Purpose: Armada 37xx Time Base Generator clock provider, exposing four fixed-factor TBG outputs.

Important APIs/functions: `armada_3700_tbg_clock_probe` registers `TBG-A-P`, `TBG-B-P`, `TBG-A-S`, and `TBG-B-S`. Helpers `tbg_get_mult` and `tbg_get_div` decode feedback, reference, and VCO divider fields.

Control flow: probe allocates onecell data for four clocks, gets the parent clock, maps registers, decodes each TBG multiplier/divider, registers fixed-factor clocks, and adds an OF provider. Remove unregisters provider and fixed factors.

State and persistence: TBG rates are derived from current hardware registers at probe and then represented as fixed-factor clocks.

Dependencies and integration: platform driver matching `marvell,armada-3700-tbg-clock`, parent XTAL clock, CCF fixed-factor registration, and periph clocks that consume TBG names.

Risks: TBG factors are not refreshed if firmware changes registers after probe. Error handling logs failed individual registrations but still publishes the provider. The error message for missing parent says "Could get" instead of "Couldn't get".

Test signals: XTAL/TBG clock tree in `clk_summary`, parent-rate variants at 25/40 MHz, remove path, and peripheral rate calculations downstream.
