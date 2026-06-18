# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-mci.h

Purpose: defines the ddbridge MCI protocol, result/command layouts, shared state structures, frontend configuration contract, and public MCI APIs.

Important APIs/types/functions: constants define MCI control, command, result, SX8 TS config, demod statuses, commands, and status values. `struct mci_command` and `struct mci_result` model firmware payloads for DVB-S/S2 search, IQ modes, input enable, signal info, and IQ samples. `struct mci_base`, `struct mci`, and `struct mci_cfg` define shared and per-frontend state. Public APIs are `ddb_mci_cmd()`, `ddb_mci_config()`, and `ddb_mci_attach()`.

Control flow: consumers fill `mci_cfg` with frontend ops and optional init callbacks, then call attach; later frontend ops issue commands through `ddb_mci_cmd()`.

State and persistence: structures describe runtime state only; firmware state exists in hardware and is controlled by commands.

Dependencies/integration: declares `ddb_max_sx8_cfg` from `ddbridge-sx8.c` and depends on DVB frontend and ddbridge core types via included context.

Risks and test signals: bitfield/layout correctness is critical because command structs are written directly as `u32` words. Test by verifying firmware responses for all command types, lock/status transitions, IQ mode configuration, and endian-sensitive fields.
