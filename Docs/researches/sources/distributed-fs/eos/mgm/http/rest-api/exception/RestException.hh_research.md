## sources/distributed-fs/eos/mgm/http/rest-api/exception/RestException.hh

Purpose: defines the base exception type for REST API errors.

Important APIs/types/functions: `RestException` derives from `common::Exception` and forwards a message string to the base class.

Control flow: derived exceptions are thrown through routing, validation, and business layers and caught by centralized error handling.

State and persistence: only stores inherited exception message/state.

Dependencies and integration points: depends on EOS namespace macros and `common/exception/Exception.hh`; included by all REST exception headers.

Risks and test signals: because generic `RestException` maps to internal server error in `HandleWithErrors`, new client-caused exceptions should derive from a more specific class or receive explicit catch handling.
