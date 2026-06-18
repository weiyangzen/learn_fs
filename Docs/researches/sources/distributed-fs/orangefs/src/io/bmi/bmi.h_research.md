<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi.h -->
## sources/distributed-fs/orangefs/src/io/bmi/bmi.h

Purpose: Public API declaration for BMI, the network abstraction used by OrangeFS clients, servers, and flow protocols.

Important APIs, types, and functions: Declares initialization/finalization, context management, expected and unexpected sends/receives, completion tests (`BMI_test`, `BMI_testsome`, `BMI_testcontext`, `BMI_testunexpected`), method-native memory allocation/free, unexpected buffer release, set/get info, address lookup/reverse lookup, wildcard range query, list-vector send/recv variants, and cancellation. `struct BMI_unexpected_info` is the public unexpected-message result with error, address, buffer, size, and tag.

Control flow and state: Header only; callers post asynchronous operations, receive `bmi_op_id_t` handles, and poll/test for completion. Context ids partition completion queues when methods support them. Unexpected messages are consumed through `BMI_testunexpected()` and later released via `BMI_unexpected_free()`.

Dependencies and integration points: Includes `bmi-types.h` and `pvfs2-internal.h`. Implemented by `bmi.c`, backed by method vtables from transports such as TCP, GM, MX, IB, RDMA, Portals, and Zoid depending on build flags.

Risks and test signals: The API relies on caller discipline for buffer lifetime, matching tags and addresses, and polling after cancel. List operations require method support and may return `BMI_ENOSYS`. Tests should validate public API contracts with at least one transport, including immediate completion return value `1`, async completion return `0`, and error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi.h -->
