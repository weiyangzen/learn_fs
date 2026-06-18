# File Research: sources/block-storage/vdo/utils/vdo/fileLayer.h

Declares constructors for file-backed `PhysicalLayer` implementations.

Key details:
- `makeFileLayer()` creates a read-write layer with expected block count.
- `makeReadOnlyFileLayer()` creates a read-only layer and computes block count from the backing file/device.
- `makeOffsetFileLayer()` creates a read-write layer with a block offset applied to all I/O.

Research relevance:
- This is the common I/O bridge for format, metadata dump, audit, and offline state utilities.
