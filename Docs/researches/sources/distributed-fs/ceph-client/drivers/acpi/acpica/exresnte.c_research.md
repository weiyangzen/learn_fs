# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exresnte.c

## Purpose
`exresnte.c` resolves namespace nodes to valued ACPICA operand objects for AML execution.

## Important APIs, Types, and Functions
The exported function is `acpi_ex_resolve_node_to_value()`. It operates on `struct acpi_namespace_node`, `union acpi_operand_object`, namespace node flags such as `ANOBJ_METHOD_ARG` and `ANOBJ_METHOD_LOCAL`, and ACPI object types. Dependencies include `acpi_ns_get_attached_object()`, `acpi_ns_get_type()`, `acpi_ds_get_package_arguments()`, `acpi_ds_get_buffer_arguments()`, and `acpi_ex_read_data_from_field()`.

## Control Flow, State, and Persistence
The function accepts a pointer to a namespace-node pointer, follows one level of alias indirection, and returns early for device, thermal, method, local, and argument pseudo-nodes. For package and buffer nodes it forces lazy argument evaluation before returning an extra reference. Strings and integers are returned with an added reference. Field-unit nodes are read immediately into a value object. Mutex, power, processor, event, and region nodes return their attached object with an added reference. Supported local references such as DDB handles, `RefOf`, and `Index` are returned as references; unsupported references and untyped nodes fail.

## Dependencies and Integration Points
This resolver is called by `acpi_ex_resolve_to_value()` and other opcode paths that turn namepaths into executable values. It integrates lazy buffer/package evaluation, namespace aliasing, and field I/O with the operand stack.

## Risks and Test Signals
Risks include alias misresolution, uninitialized-node errors, field reads happening when callers expected references, reference-count imbalance, and unsupported reference classes leaking into value paths. Tests should cover aliases, uninitialized names, package and buffer lazy evaluation, device/thermal nodes, all field kinds, mutex/event/region references, method locals/args, DDB handles, and unsupported local reference classes.
