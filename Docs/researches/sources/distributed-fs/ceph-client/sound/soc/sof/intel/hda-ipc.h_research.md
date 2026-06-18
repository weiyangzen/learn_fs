# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-ipc.h

Purpose: `hda-ipc.h` defines common sideband IPC register bit encodings for Cannonlake-style cAVS 1.8+ IPC and older cAVS 1.5 mapping, plus function prototypes for CNL IPC implementations.

Important definitions: the primary register contains a reserved doorbell bit, compact-message bit, response direction bit, and message type field. `HDA_IPC_PM_GATE` encodes the compact PM_GATE message type. The secondary register payload bits define PM behavior flags such as disabling DMA trace, preventing clock or power gating, marking active streaming, and reserved bit zero.

Control flow and integration: this header is used by `cnl.c` to compress IPC3 PM_GATE messages into sideband IPC registers and to expose CNL IPC helpers to other platform files. The definitions also document register mapping differences: primary maps to DIPCTDR/HIPCIDR in sideband IPC and DIPCT in cAVS 1.5, while secondary maps to DIPCTDD/HIPCIDD or DIPCTE.

State and persistence behavior: no runtime state is stored, but bit definitions are hardware ABI. Wrong masks or shifts would corrupt power-management IPCs and could leave DSP power gating, clock gating, or trace DMA in the wrong state.

Dependencies, risks, and test signals: the header assumes Linux bit macros and SOF/HDA types are included by consumers. Risks center on compact IPC PM flags because the DSP interprets them without mailbox payload. Test signals include CNL IPC3 PM_GATE D0I0/D0I3 transitions, trace DMA disabling during S0ix, IPC dump showing expected primary/secondary values, and compile coverage for exported CNL IPC prototypes.
