# sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-dvb.c

## Purpose
Implements DVB/ATSC transport-stream support for cx2388x cards using the cx8802 MPEG DMA engine. It allocates vb2 DVB frontend queues, attaches board-specific demodulators and tuners, controls I2C gates and shared hardware access, configures transport-stream parameters, handles LNB voltage/tone quirks, and registers DVB adapters/frontends for a large matrix of cx88 boards.

## Important APIs, Types, And Data
The module registers a `cx8802_driver` named `cx8802_dvb_driver` with type `CX88_MPEG_DVB`. Queue operations are in `dvb_qops`, backed by `queue_setup()`, `buffer_prepare()`, `buffer_finish()`, `buffer_queue()`, `start_streaming()`, and `stop_streaming()`. Important hardware arbitration helpers are `cx88_dvb_bus_ctrl()`, `cx88_dvb_gate_ctrl()`, `cx8802_dvb_advise_acquire()`, and `cx8802_dvb_advise_release()`. `dvb_register()` is the central board switch that attaches frontends and tuners.

The file contains many frontend configuration structures for MT352, ZL10353, MB86A16, CX22702, OR51132, LGDT330X, NXT200X, CX24123, S5H1409, S5H1411, XC5000, XC2028/3028, XC4000, CX24116, DS3000/TS2020, STV0900/STB6100, STV0299, STV0288/STB6000, and Samsung-specific STV0299 tuner/LNB control. Module parameters include `debug`, `dvb_buf_tscnt`, and DVB adapter numbering.

## Control Flow
Probe rejects boards without `CX88_MPEG_DVB`, probes optional VP3054 secondary I2C support, sets default TS generator control, allocates one or more frontends according to `core->board.num_frontends`, initializes one vb2 queue per frontend, names the DVB instances, and calls `dvb_register()`. Queue setup uses 188-byte TS packets grouped by four and a configurable TS packet count. Streaming starts cx8802 DMA from the first active MPEG buffer; stop cancels DMA and returns active buffers with error.

`dvb_register()` first verifies I2C availability, sets `core->gate_ctrl`, selects frontend zero, and switches on `core->boardnr`. Each case attaches the required demodulator, optional tuner, optional PLL, optional LNB controller, and board-specific operation overrides. Some boards try alternative demods for hardware revisions, disable I2C gate control so tuners remain reachable, attach XC3028/XC4000 through helper functions after opening gates, or configure multi-frontend shared DVB-S/S2 plus DVB-T devices. After successful attachments, frontend callbacks and `ts_bus_ctrl` are set, tuners are put in standby, and `vb2_dvb_register_bus()` registers adapters/frontends, optionally in shared-MFE mode.

Runtime bus acquisition flows through `cx88_dvb_bus_ctrl()`, which records the active frontend id, asks cx8802 for shared MPEG hardware, and releases it when done. Advise-acquire GPIO logic switches shared boards: HVR1300 toggles between cx23416 and cx22702 bus ownership, HVR3000/HVR4000 switch between DVB-S/S2 parallel TS and DVB-T serial TS by resetting/tri-stating demods, and WinFast DTV2000H Plus selects RF input for DVB-T.

## State And Persistence
State is held in `struct cx8802_dev`: `frontends`, active frontend id, `ts_gen_cntrl`, MPEG DMA queue, optional VP3054 adapter, and PCI/core pointers. Each `vb2_dvb_frontend` holds its DVB frontend and vb2 queue. Hardware state persists in demod/tuner I2C registers, cx88 GPIOs, TS generator control, LNB voltage/tone GPIO or I2C state, and MPEG DMA registers while active. On registration failure, the code deallocates frontends and clears `core->gate_ctrl`; remove unregisters the DVB bus and VP3054 I2C.

## Dependencies And Integration Points
The file depends on the cx88 core/cx8802 MPEG layer, V4L2/vb2 DVB helpers, many DVB frontend and tuner drivers, `dvb-pll`, board configuration from `cx88-cards.c`, tuner callback `cx88_tuner_callback()`, XC3028 setup `cx88_setup_xc3028()`, and optional `cx88-vp3054-i2c`. It shares hardware with Blackbird on some boards through cx8802 arbitration and shares the I2C bus with analog tuner subdevices through gate control.

## Risks And Test Signals
Risks include missing frontend modules, wrong board switch cases, I2C gate mismanagement, multi-frontend active-id mistakes, LNB voltage overrides not chaining previous operations, TS serial/parallel parameter mismatches, and cleanup after partial attach failures. Some board cases deliberately disable gate control or use fallback demods, making regression risk board-specific. Test signals are successful frontend registration for every supported board family, tuning/lock on DVB-T/ATSC/DVB-S/S2 as appropriate, valid TS packet flow without continuity errors, correct MFE switching on HVR3000/HVR4000, working LNB voltage/tone controls, successful VP3054 boards when configured, and clean unregister/reprobe without leaked frontends.
