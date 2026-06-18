# sources/distributed-fs/ceph-client/include/soc/fsl/qe/qe_tdm.h

Purpose: declares QE TDM mode data structures, SI RAM entry bits, SI mode fields, and setup helpers for UCC TDM users.

Important APIs and types: SI RAM macros define last/byte/count/channel-select/superframe/software-trigger/MCC/idle entries. SIxMR macros configure start address, normal/internal-loopback mode, clock/edge/gate bits, and TX/RX frame sync delay. Enums describe TX/RX timeslot direction, T1/E1 framer type, and normal/internal-loopback mode. `struct si_mode_info` holds decoded SI mode fields. `struct ucc_tdm_info` combines `ucc_fast_info` with SI settings. `struct ucc_tdm` tracks TDM port, SI RAM entry, mapped SI RAM/registers, framer/mode, timeslot count, and TX/RX masks. APIs parse DT and initialize TDM.

Control flow: a UCC TDM driver parses device-tree TDM properties, fills SI mode/UCC settings, programs SI RAM and SI registers, then initializes the UCC fast path for TDM traffic.

State and persistence: state is runtime SI RAM/register programming and `ucc_tdm` software bookkeeping. No persistent state is stored.

Dependencies and integration points: includes QE memory map, QE core, UCC, and UCC fast headers; integrates TDM-framed serial/network drivers with QE SI routing.

Risks and test signals: risks include incorrect timeslot masks, off-by-one SI RAM entries, T1/E1 framing mismatch, loopback mode leakage, and device-tree parse errors. Test T1/E1 configurations, TX/RX masks, loopback, SI RAM programming, UCC fast initialization, and start/stop under traffic.
