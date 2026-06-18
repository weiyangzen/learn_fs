# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/InterfaceAudience.java

Purpose: defines Hadoop API audience annotations that document whether program elements are public, limited-private to named projects, or private to Hadoop internals.

Important APIs, types, and functions: container class `InterfaceAudience` is annotated `@Public` and `@Evolving`. Nested runtime-retained documented annotations are `Public`, `LimitedPrivate` with `String[] value()`, and `Private`. The private constructor prevents instantiation.

Control flow: no executable flow beyond annotation metadata. Consumers attach nested annotations to packages, classes, methods, and fields; doclet filters inspect annotation mirrors by canonical name.

State and persistence: annotations are retained at runtime, so classification metadata persists in compiled class files and can be inspected reflectively or by javadoc/doclet tooling.

Dependencies and integration points: uses Java annotation APIs and integrates with Hadoop's public API policy, doclet filters, and downstream modules that mark API audience.

Risks and test signals: unannotated public classes are documented as private by policy, but enforcement relies on tooling. Test signals include annotation retention in compiled classes and doclet filtering behavior for Public, LimitedPrivate, Private, and unannotated classes.
