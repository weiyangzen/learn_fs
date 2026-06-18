# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hsmp/hsmp.c

Purpose: `hsmp.c` is the common AMD HSMP mailbox core. It validates user and in-kernel HSMP messages, serializes access per socket, sends messages through a front-end-provided read/write callback, registers `/dev/hsmp`, and provides helpers for protocol version, metrics-table mapping, and test messages.

Important APIs, types, and functions: global `hsmp_pdev` is the shared singleton. `__hsmp_send_message()` implements the mailbox protocol: clear status, write arguments, write message ID, poll response, translate firmware status codes, and read response arguments. `validate_message()` checks `hsmp_msg_desc_table` from `<asm/amd/hsmp.h>`. Exported namespace APIs include `hsmp_send_message()`, `hsmp_msg_get_nargs()`, `hsmp_test()`, `hsmp_metric_tbl_read()`, `hsmp_get_tbl_dram_base()`, `hsmp_cache_proto_ver()`, `hsmp_misc_register()`, `hsmp_misc_deregister()`, and `get_hsmp_pdev()`. `hsmp_ioctl()` is the userspace ABI through `struct hsmp_message`.

Control flow: front ends initialize `hsmp_pdev.sock[]` and each socket's `amd_hsmp_rdwr` callback. Userspace opens `/dev/hsmp` with read/write permissions that gate GET vs SET messages in `hsmp_ioctl()`. In-kernel callers call exported functions directly. The core validates message IDs, argument counts, response sizes, socket range, and reserved messages before taking `hsmp_sem` and issuing firmware mailbox transactions.

State and persistence: state is volatile: the singleton platform-device data, per-socket semaphores, mapped metric-table addresses, and cached protocol version. There is no on-disk persistence. Mailbox commands can change firmware/platform state depending on message type.

Dependencies and integration points: the file depends on `<asm/amd/hsmp.h>` for message IDs, descriptors, and metric-table structures. It integrates with miscdevice for userspace, devm ioremap in front ends for metrics, namespace exports for `hsmp_acpi`, `amd_hsmp`, and `hwmon`.

Risks: userspace ABI correctness depends on `copy_struct_from_user()` size expectations and descriptor-table accuracy. `hsmp_msg_get_nargs()` sets `response_sz` but not `num_args`, so it only works for GET-style messages whose descriptor expects zero input arguments. `hsmp_get_tbl_dram_base()` indexes `hsmp_pdev.sock[sock_ind]` without a local socket-range guard. Mailbox polling timeout and status translations directly affect user-visible error semantics.

Test signals: ioctl permission gating for read-only/write-only/read-write opens, validation failures for reserved/bad messages, concurrent per-socket serialization, firmware error-code mapping, successful TEST response value+1, metrics-table binary read size enforcement, and namespace symbol resolution.
