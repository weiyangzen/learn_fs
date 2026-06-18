# sources/distributed-fs/eos/mgm/http/rest-api/action/tape/TapeActions.hh

## Purpose
`TapeActions.hh` consolidates declarations for the tape REST action classes. It provides a single include for stage bulk request creation/query/cancel/delete, archive info lookup, and release bulk request creation.

## Important APIs, Types, and Functions
The header declares `CreateStageBulkRequest`, `GetStageBulkRequest`, `CancelStageBulkRequest`, `DeleteStageBulkRequest`, `GetArchiveInfo`, and `CreateReleaseBulkRequest`, all deriving from `TapeAction`. Constructors inject URL/method metadata, `ITapeRestApiBusiness`, input `JsonModelBuilder` instances, output `TapeRestApiJsonifier` instances where needed, and for create-stage a `TapeRestHandler` used to generate the `Location` URL.

## Control Flow
Each class overrides `run()`, implemented in the corresponding `.cc` files. The consolidated declarations let handler/factory code register actions from one header while older per-action headers can include this file or duplicate declarations.

## State and Persistence Behavior
The classes retain builder/jsonifier/business dependencies but do not store per-request state. Persistent state is owned by the bulk-request and tape business layers.

## Dependencies and Integration Points
The header depends on tape models, JSON builders/jsonifiers, `TapeRestHandler`, and the tape business interface. It is a registration and compatibility point for the tape REST API implementation.

## Risks
This file overlaps with individual action headers that declare the same class names. Include ordering and one-definition consistency are important. Constructor dependency lists are long and not null-checked, so handler setup tests need to catch missing builders/jsonifiers.

## Test Signals
Tests should compile handler registration through both consolidated and per-action includes, verify all constructors preserve method/pattern metadata, and use mocks to ensure each `run()` path calls the expected business method and response jsonifier.
