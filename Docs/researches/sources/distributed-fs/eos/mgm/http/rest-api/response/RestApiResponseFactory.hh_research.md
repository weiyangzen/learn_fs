## sources/distributed-fs/eos/mgm/http/rest-api/response/RestApiResponseFactory.hh

Purpose: compatibility header that redirects deprecated `RestApiResponseFactory.hh` includes to `RestResponseFactory.hh`.

Important APIs/types/functions: only include guard and include of `RestResponseFactory.hh`.

Control flow: no runtime behavior.

State and persistence: no state.

Dependencies and integration points: preserves older include paths during consolidation.

Risks and test signals: build tests should ensure legacy includes still compile and do not define conflicting factory names.
