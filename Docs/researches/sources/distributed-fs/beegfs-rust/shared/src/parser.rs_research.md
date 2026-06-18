## sources/distributed-fs/beegfs-rust/shared/src/parser.rs

### Purpose
Top-level module for custom parsers used by configuration and command-line deserialization.

### Important APIs, Types, and Functions
- Public submodules: `duration`, `integer_range`, and `integer_unit`.

### Control Flow and State
No runtime logic in this file beyond module exposure.

### Dependencies and Integration Points
Downstream config structs can import `parser::duration::deserialize`, `parser::integer_range::deserialize`, and `parser::integer_unit::deserialize` for serde fields.

### Risks and Edge Cases
Only exposes submodules; parser correctness and risks live in the child files.

### Test Signals
No tests in this module; child modules contain parser-specific tests.
