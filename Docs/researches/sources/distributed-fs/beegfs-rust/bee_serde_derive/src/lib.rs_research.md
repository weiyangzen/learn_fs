<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/bee_serde_derive/src/lib.rs -->
## sources/distributed-fs/beegfs-rust/bee_serde_derive/src/lib.rs

**Purpose:** Implements the `#[derive(BeeSerde)]` procedural macro that generates `Serializable` and `Deserializable` impls for BeeGFS classic message structs.

**Important APIs/types/functions:** `derive_bee_serialize` parses `DeriveInput`, calls `process_data`, and emits impls. `process_data` supports named and tuple structs. `iterate_fields` walks fields in declaration order. `build_field_actions` reads `#[bee_serde(as = TYPE)]`, emits `<TYPE>::serialize_as`/`deserialize_as` when present, or direct `crate::bee_serde::{Serializable, Deserializable}` calls otherwise.

**Control flow:** During compilation, the macro inspects struct fields, builds serialization statements in field order, and builds a `Self { field: ... }` or `Self(...)` deserializer. Unit structs, enums, and unions call `unimplemented!`, causing macro expansion failure for unsupported inputs. Attribute parsing unwraps on malformed `bee_serde` metadata.

**State and persistence behavior:** The macro defines the persistent BeeMsg field order: source struct member order becomes wire serialization order. Hints provide alternative encodings for collections, strings, and other non-primitive formats.

**Dependencies and integration points:** Depends on `syn`, `quote`, and `proc_macro2`; generated code depends on a `crate::bee_serde` module in the deriving crate. Integrates with `shared::bee_serde` helpers and all derived BeeMsg definitions.

**Risks:** Reordering struct fields is a wire-format change. Unsupported data forms fail with `unimplemented!` rather than a nice compile error. The macro only honors an `as` key; unknown `bee_serde` keys are silently ignored unless parsing fails. Generated paths are crate-relative, so deriving from a crate without the expected module layout fails.

**Test signals:** Compile named and tuple structs with and without `#[bee_serde(as = ...)]`, confirm serialization order, round-trip sample BeeMsg structs, and add compile-fail tests for enums/unit structs/malformed attributes if macro diagnostics matter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/bee_serde_derive/src/lib.rs -->
