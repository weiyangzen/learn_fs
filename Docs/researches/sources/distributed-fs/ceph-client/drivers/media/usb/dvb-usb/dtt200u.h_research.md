# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dtt200u.h

Purpose: private protocol header for DTT200U/WT220U devices. It defines debug helpers, firmware command bytes, and the custom frontend attach prototype.

Important APIs/types: `GET_*` commands read speed, tune status, RC code, configuration, AGC, SNR, Viterbi/RS error counters, and uncorrected blocks. `SET_*` commands initialize, set RF frequency/bandwidth, program/reset PID filters, and toggle streaming. `dtt200u_fe_attach()` exports the custom frontend.

Control flow: `dtt200u.c` sends power/stream/PID/RC commands, while `dtt200u-fe.c` sends tune and signal-stat commands.

State and persistence: no state is stored here; constants describe the firmware command ABI.

Dependencies and integration: includes `dvb-usb.h`, uses module debug variable from `dtt200u.c`, and connects the two DTT200U source files.

Risks: protocol is reverse-engineered and compact; command values are not self-validating. Firmware frequency unit and status byte meanings must remain synchronized with the frontend implementation.

Test signals: compile both files, USB trace GET/SET commands, tune across all supported bandwidths, PID reset, streaming switch, and RC polling.
