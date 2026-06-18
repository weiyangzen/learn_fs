# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/loadGenerator/StructureGenerator.java

## Purpose
Generates randomized directory and file structure description files consumed by `DataGenerator` and `LoadGenerator`. It models an in-memory tree, writes leaf directory paths to `dirStructure`, and writes generated file paths plus sizes to `fileStructure`.

## Important APIs, Types, and Functions
Main tunables are `maxDepth`, `minWidth`, `maxWidth`, `numOfFiles`, `avgFileSize`, `outDir`, and `seed`. Constants define default output directory, structure file names, and `_file_` prefix. `run` calls `init`, `genDirStructure`, `output`, `genFileStructure`, and `outputFiles`. The nested `INode` stores a directory name and child list with `output`, `outputFiles`, and `getLeaves`; nested `FileINode` overrides `outputFiles` and stores `numOfBlocks`.

## Control Flow
`init` parses numeric and path options, validates positive depth/file count/average size, non-negative minimum width, and `maxWidth >= minWidth`, then creates a `Random` from `-seed` or the current time. Recursive `genDirStructure(rootName, maxDepth)` decrements depth, chooses a child count in `[minWidth, maxWidth]`, chooses each child depth in roughly `[2*remainingDepth/3, remainingDepth]`, and adds `dir<i>` children. `genFileStructure` collects leaf directories and, for each requested file, picks a leaf and samples a Gaussian size shifted by `avgFileSize`, retrying until non-negative.

## State and Persistence
The generated tree is held in `root`. Persistent outputs are two local files under `outDir`: `dirStructure` and `fileStructure`. File size values are double block counts, not byte lengths; `DataGenerator` later multiplies by its `BLOCK_SIZE`.

## Dependencies and Integration Points
The generator uses Java `File`, `PrintStream`, `Random`, and Hadoop `ToolRunner.printGenericCommandUsage` for usage display. It is the producer for `DataGenerator` and indirectly for `LoadGenerator`, which depends on `_file_` naming.

## Risks and Edge Cases
`minWidth` is allowed to be zero, despite the error message saying positive, so the tree can become sparse. If no leaves are generated unexpectedly, file placement would fail. Output streams are manually closed and not guarded by try-with-resources. Gaussian sampling can loop if average size is extremely small and negative samples repeat, though termination is practically likely.

## Test Signals
Signals are structural: `dirStructure` should list leaf directories, `fileStructure` should list `_file_<n>` entries with non-negative block counts, and seeded runs should be reproducible.
