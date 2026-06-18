<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/jmx/JMXJsonServlet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/jmx/JMXJsonServlet.java

## Purpose
`JMXJsonServlet` exposes read-only JMX MBean data as JSON under Hadoop HTTP servers, supporting broad bean queries and single-attribute lookup.

## Important APIs, Types, And Functions
- `init()` stores the platform `MBeanServer` and a Jackson `JsonFactory`.
- `isInstrumentationAccessAllowed(...)` delegates access control to `HttpServer2`.
- `doTrace(...)` rejects TRACE requests.
- `doGet(...)` checks instrumentation access, sets JSON/CORS headers, parses `get` and `qry` parameters, and writes JSON.
- `listBeans(...)` queries object names, fetches MBean info/attributes, writes bean objects, and sets 400/404 status on malformed or missing resources.
- `writeAttribute(...)` filters unreadable/unsafe attribute names and serializes values.
- `writeObject(...)` serializes nulls, arrays, numbers, booleans, `CompositeData`, `TabularData`, extra subclass-defined values, and fallback strings.
- `extraCheck`/`extraWrite` are subclass extension hooks.

## Control Flow
For GET requests, access control runs first. A `get` parameter must split into exactly `ObjectName::Attribute`; otherwise the servlet writes an error and returns HTTP 400. Without `get`, `qry` defaults to `*:*`. The servlet starts a JSON object, writes a `beans` array, queries matching MBeans, skips beans that disappear or cannot be introspected, writes `name` and `modelerType`, then either writes a requested attribute or all readable safe attributes. Attribute values recurse through arrays and OpenMBean composite/tabular types.

## State And Persistence
State is servlet-local transient references to the platform MBean server and JSON factory. Responses are generated on demand; no durable persistence.

## Dependencies And Integration Points
Integrated with `HttpServer2` instrumentation authorization, servlet containers, Java ManagementFactory/MBeanServer, Jackson streaming JSON, OpenMBean types, and Hadoop web UIs.

## Risks And Edge Cases
The endpoint exposes operational state and must be protected by instrumentation access checks. Attribute getters can throw runtime exceptions or errors; the servlet logs and skips many failures. Number serialization uses `writeNumber(n.toString())`, which can fail for non-JSON numeric strings such as NaN unless subclasses intercept. Attribute names containing `=`, `:`, or space are skipped to avoid JSON/semantic issues. For single-attribute missing values, the method closes the JSON generator and sets 404 inside `listBeans`, which makes response finalization order sensitive. CORS origin is `*`.

## Test Signals
Tests should cover default and filtered queries, malformed `get`, missing attributes, composite/tabular/array serialization, forbidden instrumentation access, TRACE rejection, disappearing MBeans, unsupported getter exceptions, and subclass `extraCheck` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/jmx/JMXJsonServlet.java -->
