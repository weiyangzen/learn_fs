# sources/distributed-fs/ceph-client/drivers/phy/apple/atc.c

Purpose: Implements the Apple Silicon Type-C PHY used for USB2, USB3, USB4/Thunderbolt, and DisplayPort. It also provides the reset controller for the attached DWC3 controller and Type-C orientation/mux callbacks.

Important APIs and types: `struct apple_atcphy` is the central state object: mapped register windows, tunables, current mode, lane swap flag, DP link rate, pipehandler state, three generic PHYs, reset controller, Type-C switch/mux, and mutex. Mode data is encoded in `atcphy_modes[]`, while `dp_lr_config[]` stores DisplayPort PLL/link-rate programming. Public kernel integration is via generic PHY ops for USB2/USB3/DP, Type-C switch/mux ops, and reset-controller ops.

Control flow: probe maps named resources (`core`, `lpdptx`, `axi2af`, `usb2phy`, `pipehandler`), parses firmware tunables, forces DWC3 reset, powers USB2 and ATCPHY down, initializes the pipehandler to dummy mode, then registers reset, mux, switch, and PHY provider interfaces. Type-C mux selection maps safe/USB/USB4/TBT/DP states to internal modes. `atcphy_configure()` powers up, applies tunables, programs common overrides, optionally enables DP AUX, enables CIO3 clocks, configures lane modes/crossbar, and releases PHY reset. USB3 set-mode brings the pipehandler to USB3 after the mux has selected a compatible mode. DP configure maps link rates 1620/2700/5400/8100 to AUSPLL and lane programming.

State and persistence: `mode`, `swap_lanes`, `dp_link_rate`, and `pipehandler_up` persist in memory and gate idempotence. Hardware calibration/tuning comes from firmware-provided `apple,tunable-*` properties; without those high-speed modes are not expected to work. A mutex serializes PHY, mux, switch, and reset-controller register access.

Dependencies and integration: It depends on Type-C mux/switch/altmode definitions, USB PD/EUDO fields, generic PHY DP/USB modes, Apple tunable parsing, reset-controller framework, and reverse-engineered MMIO sequences. It matches `apple,t8103-atcphy`.

Risks and test signals: High-risk areas are undocumented magic sequences, pipehandler locking/unlocking, USB4 pipehandler fallback to USB2, Type-C orientation changes versus active modes, DP link-rate reconfiguration, and reset interactions with DWC3. Test USB2 host/device mode, USB3 host/device pipehandler setup, safe-state teardown, DP pin assignments C/D/E, DP link rates including unsupported values, Thunderbolt/USB4 mux selection, orientation reversal, missing tunables/resources, and reset assert while USB3 pipehandler is active.
