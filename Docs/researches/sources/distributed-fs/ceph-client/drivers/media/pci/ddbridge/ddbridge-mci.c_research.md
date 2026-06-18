# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-mci.c

Purpose: implements the generic ddbridge microcode interface used by MCI frontends such as MAX SX8. It serializes commands to a shared firmware block and creates DVB frontend instances backed by MCI state.

Important APIs/types/functions: `ddb_mci_cmd()` sends a full `struct mci_command` and reads `struct mci_result`; `ddb_mci_config()` writes SX8 TS config; `ddb_mci_attach()` allocates per-frontend state and shared `mci_base`. Internal `mci_reset()`, `_mci_cmd_unlocked()`, `mci_handler()`, and `match_base()` manage reset, command execution, IRQ completion, and base sharing.

Control flow: attach creates or reuses a shared base keyed by link or port, installs IRQ 0 completion, resets firmware, runs optional base/instance init, copies frontend ops, and returns the frontend. Commands take `mci_lock`, write command words, set start and done-interrupt bits, wait up to one second, then read result words.

State and persistence: `mci_list` stores shared bases for active frontends. `mci_base` holds the link, completion, locks, count, key, and type; `mci` stores frontend, demod, tuner, and number. All state is runtime-only.

Dependencies/integration: uses ddbridge link MMIO helpers, MCI register/protocol definitions, and frontend configs supplied by `ddbridge-sx8.c`.

Risks and test signals: command timeout, leaked shared bases, incorrect reference counts, and concurrent tuner/MCI locking are key risks. Test with multiple SX8 frontend opens, simultaneous tune requests, module unload after partial attach, firmware reset failure, and status command timeout injection.
