# sources/distributed-fs/ceph-client/drivers/usb/fotg210/fotg210-core.c

Purpose: provides central platform probing for the Faraday FOTG210 USB2 dual-role controller, including Gemini SoC-specific PHY/VBUS setup and dispatch to either the host controller or gadget controller subdriver.

Important APIs/functions: `fotg210_probe`, `fotg210_remove`, module init/exit, Gemini helper `fotg210_gemini_init`, and exported/shared `fotg210_vbus`. It calls subdriver hooks `fotg210_hcd_probe/remove/init/cleanup` and `fotg210_udc_probe/remove` depending on build and mode.

Control flow: probe allocates `struct fotg210`, maps MMIO, enables optional `PCLK`, reads `dr_mode`, performs Gemini syscon setup when compatible, reads the role register, warns if hardware role bits do not match requested mode, and calls UDC probe for peripheral mode or HCD probe otherwise. Remove chooses the same mode and calls the matching subdriver remove. Module init initializes HCD support if enabled and USB is not disabled, then registers the platform driver; exit unregisters and cleans up HCD support.

State and persistence: `struct fotg210` stores device, MMIO base/resource, clock, Gemini regmap, and port ID. Gemini syscon bits persistently select Mini-A/Mini-B role, VBUS, and wakeup bits in the global misc control register. `fotg210_vbus` mutates those VBUS bits at gadget-driver request.

Dependencies and integration: uses platform device resources, devm allocation and ioremap, optional clocks, OF matching, USB `dr_mode`, regmap/syscon for Gemini, string choice helpers, and host/gadget subdrivers in the same directory.

Risks: Gemini port detection relies on physical base address `0x69000000` for USB1 and treats others as USB0. There is no dynamic role switch; mode is fixed at probe. Hardware role mismatch is logged but does not abort. VBUS control silently returns for unknown port and depends on a valid syscon map. Module init ordering calls HCD global init before platform driver registration.

Test signals: probe on `faraday,fotg200`, `faraday,fotg210`, and `cortina,gemini-usb` compatible systems, host and peripheral `dr_mode`, VBUS toggling from gadget mode, wakeup-source property handling, clock enable failures, and remove/unload in both roles.
