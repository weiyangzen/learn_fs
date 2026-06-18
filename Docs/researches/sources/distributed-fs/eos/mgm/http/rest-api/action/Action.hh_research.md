# sources/distributed-fs/eos/mgm/http/rest-api/action/Action.hh

## Purpose
`Action.hh` declares the abstract base class for MGM REST actions. It binds an HTTP method and access URL pattern to a polymorphic `run()` operation.

## Important APIs, Types, and Functions
`Action` stores `mAccessURLPattern` and `mMethod`. The constructor initializes both. `run(HttpRequest*, const VirtualIdentity*)` is pure virtual and returns an owning `HttpResponse*`. `getAccessURLPattern()` and `getMethod()` expose routing metadata. The destructor is virtual.

## Control Flow
REST handlers build a set of concrete `Action` objects, match incoming requests by URL pattern and method, then call `run()` with the request and mapped identity. Concrete actions own request validation, business calls, and response creation.

## State and Persistence Behavior
The class stores only routing metadata. It does not persist request data or mutate EOS state. Persistence is delegated to concrete action business layers.

## Dependencies and Integration Points
The declaration depends on `VirtualIdentity`, common HTTP request/response/handler types, and JSONifier headers. It is extended by `TapeAction` and concrete tape REST operations.

## Risks
The response ownership contract is raw-pointer based. `run()` implementations need consistent exception handling because the base interface does not encode errors. The URL pattern string is unvalidated here, so router/action registration must keep patterns coherent.

## Test Signals
Tests should cover method/pattern getters, virtual dispatch through `Action*`, response ownership expectations, and router behavior when multiple actions share similar patterns.
