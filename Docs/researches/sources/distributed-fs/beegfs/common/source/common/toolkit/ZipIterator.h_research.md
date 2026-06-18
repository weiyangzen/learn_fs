<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/ZipIterator.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/ZipIterator.h

**Purpose:** Provides simple two- and three-container zip iterators/ranges that expose pointers to corresponding elements.

**Important APIs/types/functions:** `triple<F,S,T>`, `ZipIterator<F,S,T>`, two-value specialization `ZipIterator<F,S,void>`, `ZipIterRange`, and `ZipConstIterRange` specializations.

**Control flow:** Increment advances all underlying iterators. Dereference constructs and stores a pair/triple of pointers to current elements and returns it by reference. Range wrappers hold begin and end zip iterators and provide `operator()`, `empty`, and prefix increment for manual loops.

**State and persistence behavior:** Iterators hold underlying iterator copies and a cached pointer tuple/pair. No persistence.

**Dependencies and integration points:** Used where BeeGFS code stores related values in parallel containers, such as target IDs and states. It assumes containers have equal lengths.

**Risks:** Equality requires all underlying iterators to equal their corresponding end; if container lengths differ, loops can dereference past the shortest container. Returned pointers become invalid when containers mutate or the iterator advances. Iterator category is input-only and lacks standard post-increment/const dereference completeness. `triple` defines ordering but relies on an equality operator not declared locally.

**Test signals:** Tests should cover equal and mismatched lengths, const ranges, pointer mutation of underlying containers, and range loop idioms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/ZipIterator.h -->
