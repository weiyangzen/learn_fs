## sources/distributed-fs/ceph-client/include/linux/component.h

Purpose: This header declares the component framework used by aggregate drivers that bind only after a set of component devices is present. It is common in graphics/display pipelines and other multi-device drivers.

Important APIs, types, and functions: `struct component_ops` supplies component `bind` and `unbind` callbacks. Components register through `component_add()` or `component_add_typed()` and unregister through `component_del()`. Aggregate drivers provide `struct component_master_ops` with `bind` and `unbind`, register using `component_master_add_with_match()`, and unregister with `component_master_del()`. Match construction uses `component_match_add_release()`, `component_match_add_typed()`, and the convenience `component_match_add()`. Compare helpers include `component_compare_of`, `component_release_of`, `component_compare_dev`, and `component_compare_dev_name`. `component_bind_all()` and `component_unbind_all()` bind/unbind all matched components for a parent.

Control flow: Components register independently. An aggregate driver builds a match list and registers a master. When every required component matches, the framework calls the master `bind`, which typically allocates aggregate state, calls `component_bind_all()`, and registers the combined subsystem interface. Unregistration of the master or any component triggers master `unbind` and component unbinding.

State and persistence: Framework state is maintained in private match/component lists outside the header. Driver private aggregate state must be manually allocated and freed because its lifetime does not align with a single device; the comments explicitly warn against devm-managed aggregate resources in master bind/unbind.

Dependencies and integration points: It depends on `struct device`, OF/device matching, devm release actions for match lists, and subsystem-specific aggregate registration code.

Risks and test signals: Risks include resource lifetime leaks, partial bind rollback failures, mismatched typed vs untyped components, and unbind ordering bugs. Test signals include deferred-probe scenarios, component hot-unplug, failed component bind injection, repeated module load/unload, and aggregate driver cleanup verification.
