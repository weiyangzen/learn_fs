# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestReservedSpaceCalculator.java

## Purpose

`TestReservedSpaceCalculator` validates the reserved-space policy selection and configuration precedence for DataNode volumes. It covers absolute byte reservation, percentage reservation, conservative and aggressive combined policies, per-storage-type overrides, per-directory overrides, and invalid calculator configuration.

## Important APIs and types

- `ReservedSpaceCalculator.Builder` wires `Configuration`, mocked `DF` capacity, `StorageType`, and optional directory into a calculator instance.
- Calculator implementations under test are `ReservedSpaceCalculatorAbsolute`, `ReservedSpaceCalculatorPercentage`, `ReservedSpaceCalculatorConservative`, and `ReservedSpaceCalculatorAggressive`.
- Configuration keys include `DFS_DATANODE_DU_RESERVED_KEY`, `DFS_DATANODE_DU_RESERVED_PERCENTAGE_KEY`, and `DFS_DATANODE_DU_RESERVED_CALCULATOR_KEY`.
- `StorageType` variants include `DISK`, `SSD`, `ARCHIVE`, `NVDIMM`, and `RAM_DISK`.

## Control flow

Each test sets the calculator class in configuration, populates global, storage-type-specific, or directory-specific keys, stubs `DF.getCapacity()`, builds a calculator, and asserts `getReserved()`.

Absolute tests assert direct byte values from global and storage-type keys. Percentage tests assert capacity-derived byte values, including integer truncation. Conservative policy chooses the larger of absolute and percentage results; aggressive policy chooses the smaller. Directory tests establish precedence: directory plus storage type, directory-only, storage-type-only, then global fallback. The invalid calculator test sets the class key to a bogus string and expects `IllegalStateException`.

## State and persistence behavior

The file is stateless beyond a new `Configuration` and Mockito `DF` per test. It does not touch real disks; all capacity state is mocked. Directory paths are literal configuration suffixes, not actual filesystem locations.

## Dependencies and integration points

The calculator feeds DataNode volume capacity accounting, especially `FsVolumeImpl` availability decisions. It integrates Hadoop configuration lookup, storage-type suffix conventions, directory-specific override parsing, and `DF` capacity reporting.

## Risks and edge cases

- Directory override parsing uses raw path suffixes, so path normalization and platform separator differences are not covered.
- Negative, over-100 percentage, negative absolute, and capacity overflow cases are absent.
- The test name `testReservedSpaceAggresivePerStorageType` preserves a misspelling but still exercises the aggressive policy.
- Mocked `DF` avoids real filesystem behavior such as changing capacity during runtime.

## Test signals

Strong signals are policy-specific expected numbers, exact override precedence, multiple storage types, truncation behavior for percentages, and explicit failure on invalid calculator class configuration.
