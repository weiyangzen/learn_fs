# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestXMLUtils.java

Purpose: Security-focused tests for `XMLUtils` factory methods. The file verifies that Hadoop-created DOM, SAX, Transformer, and SAX Transformer factories parse simple XML but reject external DTD/entity inputs, reducing XXE-style exposure.

Important APIs/types/functions: Tests call `XMLUtils.newSecureDocumentBuilderFactory()`, `newSecureSAXParserFactory()`, `newSecureTransformerFactory()`, `newSecureSAXTransformerFactory()`, and `bestEffortSetAttribute()`. `getResourceStream()` loads `/xml/external-dtd.xml` and `/xml/entity-dtd.xml` test resources.

Control flow: Positive tests parse or transform `<root/>` and assert a document/output exists. Negative tests wrap parser or transformer use in `assertThrows()`, expecting `SAXException` for DOM/SAX DTD/entity parsing and `TransformerException` for external-DTD transformation. `testBestEffortSetAttribute()` mutates `AtomicBoolean` flags based on whether setting an attribute succeeds and whether the incoming flag was already false.

State and persistence behavior: No durable state. Factory instances hold security attributes/features for the life of each test. Resource streams are closed with try-with-resources in negative cases.

Dependencies and integration points: Depends on JAXP DOM/SAX/Transformer APIs, XML constants, Hadoop `XMLUtils`, AssertJ, and JUnit. The factories are integration points for any Hadoop code parsing XML configuration or test resources in a hardened way.

Risks: XML security features vary by JAXP provider; `bestEffortSetAttribute()` intentionally degrades gracefully for unsupported attributes, so platform differences are expected. These tests verify failure on included resources but do not inspect which exact feature blocks the attack or cover all entity expansion vectors.

Test signals: Successful simple parse/transform, expected exceptions for external/entity DTD inputs, and correct `AtomicBoolean` state transitions for supported/unsupported attributes are the key signals.
