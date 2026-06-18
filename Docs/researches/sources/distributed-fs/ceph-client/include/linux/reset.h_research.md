# sources/distributed-fs/ceph-client/include/linux/reset.h

Purpose: this header is the consumer-side reset-control API. It defines reset acquisition modes, optional/shared/exclusive semantics, bulk operations, managed variants, OF/fwnode helpers, and compatibility wrappers.

Important APIs/types/functions: `struct reset_control_bulk_data` stores reset IDs and handles. `enum reset_control_flags` combines shared, optional, acquired, and deasserted modes into exclusive/shared/optional/released/deasserted variants. Core APIs include reset/assert/deassert/status, acquire/release, bulk operations, `__reset_control_get()`, `__fwnode_reset_control_get()`, `reset_control_put()`, bulk get/put, `__device_reset()`, devm get/bulk get, array gets, and `reset_control_get_count()`. Many inline wrappers expose named, indexed, OF, optional, shared, exclusive, deasserted, released, devm, and array-specific forms.

Control flow: consumers acquire a reset handle, optionally acquire a temporarily released exclusive reset, assert/deassert/reset it, then release/put it. Shared resets maintain deassert counts: assert is only effective after matching deasserts, and `reset_control_reset()` is not valid on shared handles. Deasserted managed getters combine acquisition and initial deassert, with cleanup reasserting on detach.

State and persistence: the opaque `struct reset_control` state lives in reset core. This header encodes flag state passed into core acquisition and stub behavior when `CONFIG_RESET_CONTROLLER` is off. Hardware reset line state persists externally.

Dependencies and integration points: depends on bits, errors, errno, OF/fwnode, device model, reset-controller providers, and driver probe/remove sequencing.

Risks: optional APIs return `NULL` for absent resets while non-optional APIs return `ERR_PTR`; mixing those conventions is a common bug. Shared reset usage forbids assert-before-deassert and direct reset pulses. Temporarily exclusive released handles must be acquired before use. Test signals include compile tests with reset support disabled, probe paths for optional and required resets, shared deassert-count tests, devm cleanup reassertion, bulk ordering, and OF indexed lookup.
