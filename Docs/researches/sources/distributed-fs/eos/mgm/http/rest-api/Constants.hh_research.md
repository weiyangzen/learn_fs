# sources/distributed-fs/eos/mgm/http/rest-api/Constants.hh

## Purpose
`Constants.hh` centralizes a few REST API string constants used by the MGM tape REST API and URL parameter parsing.

## Important APIs, Types, and Functions
The header defines `TAPE_REST_API_SWITCH_ON_OFF` as `taperestapi.status`, `TAPE_REST_API_STAGE_SWITCH_ON_OFF` as `taperestapi.stage`, and inline `std::string URLPARAM_ID` as `{id}` inside the REST namespace.

## Control Flow
There is no runtime control flow. Other REST components include this header when checking configuration switches or extracting route parameters from URL patterns.

## State and Persistence Behavior
The constants are compile-time or inline static values. The switch names refer to external configuration state, but this header does not read or write configuration.

## Dependencies and Integration Points
It depends on `mgm/Namespace.hh` for REST namespace macros. `URLPARAM_ID` is used by stage actions with `URLParser::matchesAndExtractParameters()` to retrieve bulk request identifiers.

## Risks
String constants become part of the API/configuration contract. Renaming either tape switch or the `{id}` token without migrating router/business code would silently break feature toggles or parameter extraction.

## Test Signals
Tests should verify route templates and action code use the same `{id}` token, and configuration tests should assert both tape REST switch names match documented MGM configuration keys.
