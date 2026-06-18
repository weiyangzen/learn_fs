# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/mock_engine.h

Purpose: declares the mock i915 engine type and its public construction/control functions for selftests.

Important APIs/types: `struct mock_engine` embeds `struct intel_engine_cs base` and adds `hw_lock`, `hw_queue`, and `hw_delay`. Public functions are `mock_engine()`, `mock_engine_init()`, `mock_engine_flush()`, `mock_engine_reset()`, and `mock_engine_free()`.

Control flow: no executable flow in the header. Consumers create an engine with `mock_engine()`, initialize it with `mock_engine_init()`, flush queued fake work, reset as needed, and free via the declared cleanup hook.

State and persistence behavior: the embedded base object lets mock engines be passed anywhere an `intel_engine_cs` is expected. The added queue/timer state persists pending fake hardware work between submission and completion.

Dependencies and integration points: includes Linux list/spinlock/timer primitives and `gt/intel_engine.h`, making it part of the i915 GT test harness. It bridges generic engine code and mock-specific queue simulation.

Risks: the header declares `mock_engine_free()` but the inspected C file does not define it, so either another object provides it or the declaration is stale. Because `struct mock_engine` is layout-visible, changes must remain aligned with `container_of()` uses in the implementation.

Test signals: compile/link coverage validates the declared API. Mock selftests exercise the queue/timer fields and embedded base compatibility.
