# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_cmd.h

Purpose: Declares IPA immediate-command opcodes and the command-building API used by IPA setup, table, memory, and endpoint code.

Important APIs/types: `enum ipa_cmd_opcode` defines hardware opcodes for IPv4/IPv6 filter and route table init, header init, register write, IP packet init, DMA shared memory, packet tag status, and `IPA_CMD_NONE` for non-command transfer TREs. Function declarations cover validation, command-channel pool lifecycle, table/header/register/DMA command append, pipeline clear, command transaction allocation, and command subsystem init.

Control flow and integration: Callers allocate a command transaction with `ipa_cmd_trans_alloc()`, append one or more commands using the add helpers, and commit synchronously through GSI transaction APIs. Setup uses validation helpers before programming memory-backed tables. Pipeline clear is used when hardware state must drain before continuing.

State and persistence: Header declares no state. The implementation mutates command-channel DMA pools and IPA/GSI hardware state.

Dependencies: Forward-declares GSI channel/transaction, IPA, and IPA memory structs. Includes Linux types. `gsi_trans.h` includes this header for opcode values, so include cycles are deliberately minimized.

Risks: Opcode numeric values are hardware ABI and must not change without matching hardware documentation. `IPA_CMD_NONE` is a sentinel used by GSI transaction formatting to emit a normal transfer TRE; treating it as a real immediate command would be incorrect. Callers must respect `IPA_COMMAND_TRANS_TRE_MAX` from `gsi_trans.h`.

Test signals: Compile coverage for all command users, immediate-command smoke during setup, route/filter table init, pipeline clear completion, and DMA shared-memory read/write checks.
