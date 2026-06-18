# sources/distributed-fs/ceph-client/drivers/gpu/vga/vga_switcheroo.c

Purpose: Linux hybrid graphics coordination subsystem for laptops with muxed or muxless dual GPUs. It coordinates GPU clients, audio clients, mux/power handlers, debugfs user commands, DDC switching, delayed switches, and runtime PM power switching.

Important APIs and functions: exported APIs include handler registration/unregistration, client/audio-client registration, probe-defer checks, client state lookup, framebuffer association, DDC lock/unlock, delayed-switch processing, and runtime-PM domain helpers. Internal state lives in `struct vgasr_priv`; clients are `struct vga_switcheroo_client`.

Control flow: switcheroo becomes active once two VGA clients and a handler are registered. Debugfs `switch` parses `OFF`, `ON`, `IGD`, `DIS`, delayed variants, and mux-only variants. Full switching runs stage 1 to power on the target and set default VGA device, then stage 2 to mark active state, remap fbcon, call handler `switchto`, reprobe, power off old client, and update audio state. Delayed switches store target state until clients report switchability.

State and persistence: singleton global `vgasr_priv` tracks active status, clients, handler callbacks, handler flags, debugfs root, delayed target, and DDC owner. State is protected by `vgasr_mutex` and `mux_hw_lock`.

Dependencies and integration: integrates with PCI, ACPI/apple-gmux, fbcon, debugfs, VGA arb, runtime PM, HDA audio clients, and DRM/fb GPU drivers through `vga_switcheroo_client_ops` and handler callbacks.

Risks: global singleton design limits multi-instance systems. Lock ordering around global mutex and mux lock is critical. Debugfs commands are low-level and can blank displays on mux-only switching. Runtime PM mode makes manual ON/OFF no-ops for driver-managed clients.

Test signals: practical signals are debugfs state output, successful GPU switch with fbcon remap, delayed switch completion after clients close, DDC EDID probing for inactive GPU, runtime suspend/resume power handler calls, and absence of client refusal logs.
