# sources/distributed-fs/ceph/src/rgw/driver/rados/config/impl.h

Purpose: Declares `ConfigImpl`, the shared low-level RADOS utility for the config store, plus create-mode semantics and templated encode/decode/list helpers.

Important APIs/types/functions: `enum class Create` documents create preconditions. `ConfigImpl` owns a librados client and root pools for realms, periods, zonegroups, and zones. Templated `read<T>()` decodes from a bufferlist with `-EIO` on decode error. Templated `write<T>()` encodes data before write. `list()` scans pool object names from a RADOS cursor and applies a caller-supplied oid-to-entry filter.

Control flow: `list()` parses the marker into `librados::ObjectCursor`, iterates `nobjects_begin()` until the output span is full or the pool ends, filters oids, and returns entries as a subspan plus a next cursor string.

State/persistence: The header defines no schema but establishes full-object encoded persistence and object-name listing as the abstraction for all config metadata.

Dependencies/integration: Includes librados, RGW basic types/tools, SAL config interfaces, `std::span`, and C++20 concepts for `std::regular_invocable`. It is included by all config entity implementation files.

Risks: `list()` advances the cursor on every object, including filtered-out ones; callers with sparse prefixes may need repeated calls to fill pages. Bad marker strings return `-EINVAL`. Any exception from object iteration is collapsed to `-EIO`.

Test signals: Unit tests should cover bad markers, sparse filtering, empty pages with nonempty next cursors, decode corruption, and all `Create` modes through the concrete implementation.
