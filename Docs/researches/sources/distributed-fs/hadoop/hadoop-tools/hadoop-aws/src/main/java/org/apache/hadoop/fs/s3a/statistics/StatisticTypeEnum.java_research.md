<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/StatisticTypeEnum.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/StatisticTypeEnum.java

Purpose: enum describing statistic value categories.

Important APIs/types/functions: values are `TYPE_COUNTER`, `TYPE_DURATION`, `TYPE_GAUGE`, and `TYPE_QUANTILE`.

Control flow: none in this file; other metadata/config code can use these values to classify statistics.

State/persistence: static enum constants only.

Dependencies/integration: part of S3A statistics API.

Risks/test signals: adding/removing enum values affects metadata consumers. Tests should cover mappings from `Statistic` definitions to these categories where used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/StatisticTypeEnum.java -->
