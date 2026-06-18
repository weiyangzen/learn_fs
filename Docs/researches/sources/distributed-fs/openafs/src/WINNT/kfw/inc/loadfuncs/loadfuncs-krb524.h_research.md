# sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-krb524.h

## Purpose

This small header declares dynamic bindings for the Kerberos 5 to Kerberos 4 conversion DLL, `krb524.dll`. It supports compatibility code that needs to convert a KRB5 credential into a KRB4 `CREDENTIALS` record.

## Important APIs, Types, and Functions

- `KRB524_DLL` names `krb524.dll`.
- `krb524_init_ets(krb5_context)` initializes error tables for the conversion library.
- `krb524_convert_creds_kdc(krb5_context, krb5_creds *, CREDENTIALS *)` converts KRB5 credentials to KRB4 credentials through the KDC path.

## Control Flow

The file contributes two symbol typedefs to a dynamic load table. Callers first load `krb524.dll`, initialize error tables, then call the conversion function when a KRB4 credential is needed from a KRB5 credential.

## State and Persistence Behavior

The header itself stores no state. The external DLL may initialize process-local error-table state, and conversion depends on the caller-provided `krb5_context`, KDC configuration, and output `CREDENTIALS` storage. The conversion result may be saved later by KRB4 ticket APIs, but this header does not perform persistence.

## Dependencies and Integration Points

Depends on `loadfuncs.h`, `<krb5.h>`, and `<krb.h>`. It bridges the KRB5 and KRB4 compatibility layers used by OpenAFS Windows code that still needs KRB4 token/ticket support.

## Risks

- The KRB524 compatibility path may be absent on modern Kerberos installations.
- KRB4 output credentials are legacy-sensitive material and should be handled as short-lived compatibility artifacts.
- Conversion may require KDC support and network reachability; callers should distinguish load failure, conversion failure, and KDC policy failure.

## Test Signals

Test missing-DLL behavior and successful symbol resolution independently. If a test KDC supports KRB524 conversion, verify a known KRB5 credential converts to a KRB4 `CREDENTIALS` object and that failure paths leave the destination structure in a predictable state.
