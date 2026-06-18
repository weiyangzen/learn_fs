# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-dvb.c

## Purpose
This file provides DVB support for cx18 hybrid cards. It registers DVB adapters/demux devices, attaches board-specific demodulator and tuner frontends, and starts/stops transport stream DMA in response to DVB feed activity.

## Important APIs, Types, and Functions
Public functions are `cx18_dvb_register()` and `cx18_dvb_unregister()`. DVB callbacks are `cx18_dvb_start_feed()` and `cx18_dvb_stop_feed()`. Frontend attach flow lives in static `dvb_register()`. Board-specific config objects cover S5H1409/MXL5005S, S5H1411/TDA18271, ZL10353/XC2028, and MT352 firmware-assisted initialization. `yuan_mpc718_mt352_init()` programs MT352 register pairs from `dvb-cx18-mpc718-mt352.fw`.

## Control Flow
Registration creates a DVB adapter, software demux, dmxdev, hardware and memory frontends, connects the hardware frontend, attaches the physical frontend based on `cx->card->type`, registers it, enables the TS demux clock, and initializes DVB networking. Starting the first feed ensures cx18 firmware is initialized, programs serial DMUX mode for HVR-1600 cards, and starts the TS stream through `cx18_start_v4l2_encode_stream()`. Stopping the last feed stops the encode stream.

## State and Persistence
Per-stream `struct cx18_dvb` stores adapter, demux, dmxdev, frontend, net, feed count, enabled flag, and feed lock. Feed count is volatile and gates DMA start/stop. Frontend firmware state is held by attached demod/tuner drivers.

## Dependencies and Integration Points
The file depends on DVB core, frontend drivers, firmware loading, cx18 streams, I2C adapters, card type tables, GPIO tuner reset callbacks, and MMIO clock/DMUX registers.

## Risks and Edge Cases
Some board support is experimental. MPC718 MT352 requires an external firmware-derived register sequence and enforces a small even firmware size. Start/stop feed reference counting must stay balanced. `dvb_register()` returns `-1` on frontend absence rather than a specific errno. TS DMUX clock and serial/parallel mode settings are board-specific.

## Test Signals
Confirm adapter/frontend registration per hybrid board, firmware-missing behavior on MPC718 MT352, channel scan and lock, feed start/stop under multiple PIDs, module unload after DVB use, and no analog/DVB stream contention beyond documented card limitations.
