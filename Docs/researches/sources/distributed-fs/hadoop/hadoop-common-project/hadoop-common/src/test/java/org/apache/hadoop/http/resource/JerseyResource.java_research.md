<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/resource/JerseyResource.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/resource/JerseyResource.java

## Purpose
Small Jersey resource used by HTTP server tests. It echoes the matched request path and `op` query parameter as JSON so tests can validate Jersey routing and response encoding inside Hadoop's embedded Jetty stack.

## Important APIs, Types, and Functions
Annotated with `@Path("")`; `get()` is a `@GET` handler for `@Path("{path:.*}")` and produces `application/json` with `JettyUtils.UTF_8`. It uses `@PathParam(PATH)` and `@QueryParam(OP)` with default values, builds a `TreeMap`, serializes it via Jetty `JSON.toString`, and returns `Response.ok(js).type(MediaType.APPLICATION_JSON).build()`.

## Control Flow and State
The resource is stateless aside from logging. Each request logs path/op, inserts them into a deterministic sorted map, serializes JSON, and returns a 200 response.

## Dependencies and Integration Points
Integrates JAX-RS annotations, Jetty JSON utility, Hadoop's `JettyUtils` charset constant, and test HTTP server Jersey configuration.

## Risks and Test Signals
Risks are catch-all path matching, default-value semantics, JSON ordering, and response content type/charset. Downstream tests can assert exact JSON keys `path` and `op` and content type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/resource/JerseyResource.java -->
