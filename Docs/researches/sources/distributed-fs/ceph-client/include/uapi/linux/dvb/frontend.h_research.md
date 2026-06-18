## sources/distributed-fs/ceph-client/include/uapi/linux/dvb/frontend.h

Purpose: This header defines the DVB frontend tuning and status ABI. It covers frontend capabilities, DiSEqC/LNB control, signal status, DVBv5 property arrays, statistics, and deprecated DVBv3 tuning structures.

Important APIs and types: `enum fe_caps` reports modulation, FEC, inversion, auto-detection, multistream, second-generation modulation, recovery, and TS muting support. `struct dvb_frontend_info` reports name, frequency/symbol-rate ranges, and caps, with deprecated single frontend type. DiSEqC structures carry master commands and slave replies. Enums define voltage, tone, mini-burst, lock status, inversion, FEC, modulation, transmission mode, guard interval, hierarchy, interleaving, pilot, rolloff, and delivery system. DVBv5 properties are carried by `struct dtv_property` and `struct dtv_properties`, with commands from `DTV_FREQUENCY` through `DTV_STAT_*` and `DTV_ENUM_DELSYS`. `struct dtv_fe_stats` stores up to four scaled stats.

Control flow and state: Modern userspace queries `FE_GET_INFO` and `DTV_ENUM_DELSYS`, sets a batch of DVBv5 properties with `FE_SET_PROPERTY`, triggers tune with `DTV_TUNE`, and monitors `FE_READ_STATUS`, `FE_GET_EVENT`, and quality stats. Satellite flows also set LNB voltage/tone and send DiSEqC commands. `FE_TUNE_MODE_ONESHOT` disables normal zigzag tuning and event monitoring until reopened read-write.

Persistence and dependencies: Tuning parameters, DiSEqC/tone/voltage, and frontend state live in tuner/demod hardware and the kernel frontend device. The header depends on `<linux/types.h>`.

Integration points: It drives demux input: a locked frontend supplies MPEG-TS PIDs to `dvb/dmx.h`, then audio/video/net/CA layers consume streams. It also integrates with libdvbv5 and legacy DVBv3 applications.

Risks and test signals: Risks include mixed DVBv3/DVBv5 usage, unit differences for satellite frequency, unsupported property combinations, packed struct ABI, stats scale interpretation, and auto-detection fallback behavior. Tests should tune representative DVB-S/S2, DVB-T/T2, DVB-C, ATSC, ISDB, and DTMB configurations; validate `DTV_IOCTL_MAX_MSGS`; read layered stats; test DiSEqC timeouts; verify event generation; and confirm deprecated ioctls remain compatible.
