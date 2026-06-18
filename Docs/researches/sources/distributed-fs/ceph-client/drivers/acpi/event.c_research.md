# sources/distributed-fs/ceph-client/drivers/acpi/event.c

Purpose: `event.c` provides kernel ACPI event fan-out. It maintains a blocking notifier chain for in-kernel consumers and, when networking is enabled, registers a generic netlink family named `acpi_event` to multicast ACPI events to userspace.

Important APIs, types, and functions: exported notifier APIs are `acpi_notifier_call_chain()`, `register_acpi_notifier()`, and `unregister_acpi_notifier()`. Exported userspace event API is `acpi_bus_generate_netlink_event()`. The netlink payload type is `struct acpi_genl_event`; family constants describe the `ACPI_GENL_ATTR_EVENT` attribute and `ACPI_GENL_CMD_EVENT` command.

Control flow: ACPI event producers call `acpi_notifier_call_chain()` with a device class, bus id, type, and data, which fills `struct acpi_bus_event` and invokes the blocking chain. For netlink, producers allocate an skb in atomic context, add a genetlink header, reserve a payload attribute, fill event fields, close the message, and multicast it to the ACPI multicast group. `fs_initcall(acpi_event_init)` registers the genetlink family unless ACPI is disabled.

State and persistence: state is process lifetime only: the notifier chain head, a monotonically increasing `acpi_event_seqnum`, and the registered genetlink family. Events are not stored or replayed.

Dependencies and integration: this file integrates ACPI bus events with both kernel notifiers and userspace generic netlink. It is used by drivers such as the ACPI fan driver to emit state-change events.

Risks: netlink allocation uses `GFP_ATOMIC` and can fail under pressure, losing events. `bus_id` is fixed at 15 bytes in the netlink payload, so identifiers may be truncated. Notifier callbacks run in a blocking notifier context and can delay the event source.

Test signals: verify genetlink family registration, multicast receive from userspace, event field truncation behavior, no-op stub behavior without `CONFIG_NET`, notifier registration/unregistration, and event generation while ACPI is disabled.
