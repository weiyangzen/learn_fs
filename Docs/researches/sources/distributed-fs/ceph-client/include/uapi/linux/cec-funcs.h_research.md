
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/cec-funcs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/cec-funcs.h

## Purpose
Provides inline helper functions and operand structs for building and decoding HDMI CEC messages. It covers One Touch Play, Routing Control, Standby, recording and timer programming, system information, deck and tuner control, vendor commands, OSD/menu/user-control, power, feature abort, system audio, ARC, dynamic audio latency, and CDC/HEC/HPD messages.

## APIs, Control Flow, and State
The header is a large inline encoder/decoder library around `struct cec_msg` from `<linux/cec.h>`. Functions named `cec_msg_*` set `msg->len`, opcode bytes, operands, broadcast destination bits, and expected `msg->reply`; matching `cec_ops_*` functions decode operands from received messages. Helper structs include digital-service identifiers, record sources, tuner-device info, UI commands, and CDC-related operands. Control flow is mostly switch-based operand packing for record sources, digital service IDs, UI optional operands, timer status duration fields, CEC version feature blocks, tuner analog/digital forms, and variable-length CDC/HEC physical-address lists. The header stores no durable state, but it mutates caller-provided `struct cec_msg` buffers; persistent CEC adapter state, logical addresses, pending replies, and topology live in the CEC framework and devices.

## Dependencies, Integration, Risks, and Tests
Depends on the opcode/operand constants and helpers in `linux/cec.h`. Integration points are V4L2 CEC adapters, HDMI device-control daemons, cec-ctl/libcec-style tools, CEC compliance testing, and kernel drivers that emit or parse CEC messages. Risks include caller-provided buffers being too small or not initialized with source/destination nibbles, missing message-length validation before `cec_ops_*` reads operands, BCD time packing accepting invalid values, variable-length string/vendor/audio descriptor truncation, subtle reply-opcode expectations, and protocol bugs in rarely used CDC/HEC helpers. Test signals include CEC compliance suites, encode/decode round trips for every opcode family, fuzzing short `msg->len` inputs, broadcast vs directed address checks, reply expectation tests, and HDMI topology tests for ARC, routing, power, and CDC messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/cec-funcs.h -->
