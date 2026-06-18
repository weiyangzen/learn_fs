<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi-method-support.c -->
## sources/distributed-fs/orangefs/src/io/bmi/bmi-method-support.c

Purpose: Implements shared allocation and parsing helpers used by BMI transport methods.

Important APIs, types, and functions: `bmi_alloc_method_op()` allocates a zeroed `method_op_st` plus method-private payload, registers an op id with `id_gen_fast_register`, and points `method_data` after the generic struct. `bmi_dealloc_method_op()` unregisters and frees it. `bmi_alloc_method_addr()` allocates a contiguous `bmi_method_addr` plus method-private payload and sets `method_type`. `bmi_dealloc_method_addr()` frees it. `string_key()` extracts the address payload for a protocol key from a comma/whitespace separated BMI URL list, allowing `protocol-subzone://target`.

Control flow and state: Allocation helpers create contiguous in-memory objects and rely on the global id generator for operation lookup persistence. `string_key()` loops through possible protocol occurrences, validates exact protocol name or optional subzone, requires `://`, and returns a newly allocated substring up to comma or whitespace.

Dependencies and integration points: Uses `id-generator`, `reference-list`, `quicklist` structures defined in `bmi-method-support.h`, and `gossip` for the surrounding BMI environment. GM and other methods depend on the contiguous layout to recover method payloads.

Risks and test signals: `method_data` pointer arithmetic assumes no alignment-sensitive payload beyond malloc's base alignment. `string_key()` is hand-written parsing and rejects many punctuation characters in subzones. Tests should cover duplicate keys, subzones, malformed delimiters, allocation failure, and op-id unregister on deallocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi-method-support.c -->
