# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/ECPolicyLoader.java

Purpose: `ECPolicyLoader` loads user-defined HDFS erasure-coding policies from an XML configuration file.

Important APIs/types/functions: `loadPolicy(String)` resolves the file, returns empty list when missing, and wraps parser/IO/SAX failures in `RuntimeException`. `loadECPolicies(File)` parses secure XML and enforces `<configuration>`, `<layoutversion>`, `<schemas>`, and `<policies>`. `loadLayoutVersion()` validates version 1. `loadSchemas()` parses unique `ECSchema`s by id. `loadPolicies()` parses policy elements and skips duplicate policies with a warning. `getPolicyFile()` requires relative/classpath URLs to be local file URLs. `loadSchema()` maps `<k>`/`<m>` to ECSchema option names. `loadPolicy(Element, Map)` resolves schema references and positive integer cell size.

Control flow: loading is strict for structural errors and unknown elements under schemas/policies. Schema duplicates throw; policy duplicates warn. Missing schema or non-positive/invalid cell size throws.

State and persistence behavior: stateless loader; all data is returned as a list of `ErasureCodingPolicy`. No caching.

Dependencies and integration points: depends on secure `XMLUtils`, DOM APIs, `ECSchema`, and `ErasureCodingPolicy`. Integrates with NameNode/client configuration paths for custom EC policy definition.

Risks and test signals: `getPolicyFile` constructs `new URL(policyFilePath)` for non-absolute paths, so plain relative filesystem paths may fail unless passed as URL-like values. Error wrapping loses original exception cause. Tests should cover valid config, missing file, bad root/version/missing sections, duplicate schema/policy behavior, k/m alias mapping, schema reference failure, bad cell size, non-file URL rejection, and secure XML parser behavior.
