# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/MetaBlockAlreadyExists.java

Purpose: checked exception indicating an attempt to create a duplicate named BCFile/TFile meta block.

Important APIs/types/functions: class extends `IOException`; package-private constructor accepting a message.

Control flow: `BCFile.Writer.prepareMetaBlock()` throws it when `MetaIndex` already has the requested name.

State and persistence: exception instance only.

Dependencies and integration: public stable API class in `org.apache.hadoop.io.file.tfile`, but construction is package-private, so TFile/BCFile code controls emission.

Risks: callers can catch the public type but cannot construct it directly. Tests should verify duplicate meta block creation throws this subtype and leaves writer state consistent.
