# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-smbios.h

Purpose: Shared Dell SMBIOS client/backend interface.

Important APIs/types/functions: Defines Dell SMBIOS classes/selects, kernel-reserved token IDs, `struct calling_interface_token`, `struct calling_interface_structure`, call helpers, token lookup, laptop notifier API, class support, and backend init/exit declarations with stubs.

Control flow/state/persistence: Header-only; state is in `dell-smbios-base.c` and backends.

Dependencies/integration: Used by Dell laptop, PC, WMI backend, and SMM backend. Pulls in uapi WMI calling-interface buffer types.

Risks/test signals: Token constants are shared behavioral contract. Build-test WMI-only, SMM-only, both, and stub configurations.
