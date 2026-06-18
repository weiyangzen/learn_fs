# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/XMLUtils.java

Purpose: `XMLUtils` centralizes secure XML/XSLT factory creation and a stylesheet transformation helper to reduce XXE and external-resource exposure.

Important APIs/types/functions: constants name JAXP/SAX security features. `transform(InputStream, InputStream, Writer)` applies an XSLT stylesheet using a secure transformer factory. `newSecureDocumentBuilderFactory`, `newSecureSAXParserFactory`, `newSecureTransformerFactory`, and `newSecureSAXTransformerFactory` create configured factories. `bestEffortSetAttribute` and `setOptionalSecureTransformerAttributes` set external DTD/stylesheet access restrictions when supported.

Control flow: parser factories enable `FEATURE_SECURE_PROCESSING`, disallow doctype declarations, disable external DTD loading and external entity resolution, and for DOM disable entity reference node creation. Transformer factories enable secure processing and then attempt optional external-access attributes. Unsupported optional attributes flip static `AtomicBoolean` flags to avoid repeated attempts.

State and persistence behavior: two static atomic flags remember whether the JVM transformer supports optional attributes. No XML data is persisted by the utility.

Dependencies and integration points: depends on JAXP DOM/SAX/transform APIs, SLF4J, and XML SAX exceptions. Tests and Hadoop code parsing XML configuration or servlet output should use these factories.

Risks: optional transformer attributes are best-effort; on unsupported runtimes the class logs at debug and proceeds with only secure processing. `transform` accepts arbitrary stylesheet and XML streams, so security depends on the configured factory and caller-controlled inputs. Factories may throw if a parser implementation does not support required features.

Test signals: existing `TestXMLUtils` references secure DOM parsing. Tests should include XXE/doctype rejection, disabled external entities, transformer external access behavior, and fallback when optional attributes are unsupported.
