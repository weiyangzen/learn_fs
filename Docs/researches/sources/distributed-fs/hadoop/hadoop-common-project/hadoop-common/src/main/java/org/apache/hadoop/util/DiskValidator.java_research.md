# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/DiskValidator.java

Purpose: `DiskValidator` is the pluggable interface for checking whether a local disk directory is usable.

Important APIs and types: single method `checkStatus(File dir) throws DiskErrorException`.

Control flow: implementations perform whatever validation they need and throw on failure. `BasicDiskValidator` performs access checks; `ReadWriteDiskValidator` is also supported by the factory outside this item.

State and persistence behavior: interface-only. Implementations may create directories or write probe files depending on validation strategy.

Dependencies and integration points: used by `DiskValidatorFactory` and storage-directory checking components. It depends on `DiskChecker.DiskErrorException`.

Risks: implementations can have side effects, so callers must understand the chosen validator. Failure classification is coarse through `DiskErrorException`.

Test signals: verify factory-created implementations respect this contract and callers handle thrown `DiskErrorException`.
