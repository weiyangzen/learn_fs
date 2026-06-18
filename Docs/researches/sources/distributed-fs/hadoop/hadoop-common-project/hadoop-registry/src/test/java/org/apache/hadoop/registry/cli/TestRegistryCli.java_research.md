# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/cli/TestRegistryCli.java

Purpose: validates the command-line registry client against a live in-memory registry from `AbstractRegistryTest`.

Important APIs and functions: `setUp()` creates captured stdout/stderr streams and instantiates `RegistryCli`; `assertResult()` checks CLI exit codes; tests cover bad command names, invalid argument counts, invalid argument values, bad paths, missing paths, and successful `bind`, `resolve`, `rm`, and `mknode` flows.

Control flow: valid command tests repeatedly bind records of `-inet`, `-webui`, and `-rest` endpoint forms, resolve them, remove them, and confirm subsequent resolution fails. It also tests binding records under subdirectories and binding directly to an existing directory node.

State and persistence: all CLI actions mutate the registry service created by the superclass. The test captures output but only asserts status codes, not emitted text.

Dependencies and integration: integrates `RegistryCli`, registry operations, registry configuration, endpoint parser options, and JUnit lifecycle. It indirectly exercises service record creation by CLI command parsing.

Risks and test signals: strong coverage for command validation and basic registry mutation. It does not verify output formatting, stderr diagnostics, or stream restoration after `System.setOut(sysOut)`, so global stdout side effects are a possible test hygiene risk.
