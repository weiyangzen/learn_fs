<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_iter.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_iter.rs

Purpose: provides iterators and lookup helpers over all registered nexus bdevs in the SPDK `NexusModule`.

Important APIs/types/functions: `nexus_iter`, `nexus_iter_mut`, `nexus_lookup`, `nexus_lookup_mut`, `nexus_lookup_name_uuid`, `nexus_lookup_uuid_mut`, `nexus_lookup_nqn`, `nexus_lookup_nqn_mut`, `NexusIter`, and `NexusIterMut`.

Control flow: immutable and mutable iterators wrap `BdevModuleIter<Nexus>`. Lookup helpers create a fresh iterator and find by nexus name, UUID, name-or-UUID, or a name parsed from NQN text. Mutable iteration returns pinned mutable nexus references from bdev data.

State and persistence: no state is stored here. The live SPDK bdev module registry is the source of truth. NQN lookup parses the substring after the first colon as a nexus name.

Dependencies/integration: depends on `NexusModule::current`, `spdk_rs::BdevModuleIter`, and the `Nexus` bdev data type. It is used throughout nexus creation, rebuild callbacks, snapshot tasks, child event handlers, and self-shutdown paths.

Risks: `NexusModule::current()` panics if the module is not registered. NQN parsing is simplistic and may mis-handle NQNs with unexpected colon structure. Mutable lookups expose pinned mutable references, so callers must respect reactor/thread ownership and avoid aliasing with other references.

Test signals: lookup by name, UUID, name-or-UUID collision behavior, mutable lookup state mutation, NQN parsing for expected and malformed NQNs, empty module iteration, and behavior before module registration.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_iter.rs -->
