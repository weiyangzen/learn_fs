<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/storage/striping/Raid10Pattern.h -->
## sources/distributed-fs/beegfs/client_module/source/common/storage/striping/Raid10Pattern.h

**Purpose:** Declares and inline-constructs the RAID10 stripe-pattern subclass. **APIs/types:** `Raid10Pattern` embeds `StripePattern` and owns `stripeTargetIDs` plus `mirrorTargetIDs`; inline init/construct/uninit assign virtual methods including mirror-target access. **Control flow/state:** intended mainly for deserialization from chunk size, with vectors filled by `Raid10Pattern_deserializePattern`. **Dependencies/integration:** uses `StripePattern` polymorphism and `UInt16Vec`. **Risks/tests:** both vectors must be released on uninit; tests should cover virtual dispatch and cleanup after failed deserialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/storage/striping/Raid10Pattern.h -->
