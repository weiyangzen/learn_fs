<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/storage/striping/SimplePattern.h -->
## sources/distributed-fs/beegfs/client_module/source/common/storage/striping/SimplePattern.h

**Purpose:** Declares the simple/invalid stripe-pattern subclass. **APIs/types:** `SimplePattern` embeds `StripePattern`; inline init/construct/uninit and virtual assignment configure no-op methods for deserialize, target lookup, target IDs, and counts. **Control flow/state:** construction only records the pattern type and chunk size; no extra state is owned. **Dependencies/integration:** used as fallback by base stripe-pattern creation. **Risks/tests:** because uninit is empty, adding fields later requires updating cleanup; tests should cover invalid construction and virtual destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/storage/striping/SimplePattern.h -->
